"""
Regex Security Scanner для Claude Skills.
Первый уровень проверки — до AI-анализа.
"""

import re
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# ─── Конфигурация путей ────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
INCOMING_DIR = BASE_DIR / "incoming-skills"
QUARANTINE_DIR = BASE_DIR / "security" / "quarantine"
LOG_FILE = BASE_DIR / "security" / "log.txt"

# ─── Паттерны угроз ───────────────────────────────────────────────────────────

THREAT_PATTERNS = {
    "prompt_injection": [
        r"ignore\s+previous\s+instructions",
        r"override\s+system",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"forget\s+(everything|all)\s+(you|i)\s+(know|said|told)",
        r"new\s+instructions\s*:",
        r"system\s+prompt\s*:",
        r"you\s+are\s+now\s+(?!a\s+content)",  # исключаем легитимные "you are now a content..."
        r"act\s+as\s+if\s+you\s+(have\s+no|don't\s+have)",
        r"DAN\s+mode",
        r"jailbreak",
    ],
    "data_exfiltration": [
        r"send\s+data",
        r"exfiltrate",
        r"transmit\s+(the\s+)?(user|system|private|secret)",
        r"leak\s+(the\s+)?(data|information|credentials)",
        r"steal\s+(the\s+)?(data|token|key)",
        r"http[s]?://(?!schema\.org|json-ld\.org)",  # разрешаем безопасные schema URL
        r"POST\s+.*(?:password|token|secret|key)",
    ],
    "network_calls": [
        r"\bcurl\b",
        r"\bwget\b",
        r"\bfetch\s*\(",
        r"requests\.(?:get|post|put|delete|patch)",
        r"urllib\.request",
        r"http\.client",
        r"xmlhttprequest",
        r"axios\.",
    ],
    "code_execution": [
        r"\bsubprocess\b",
        r"\bos\.system\s*\(",
        r"\bos\.popen\s*\(",
        r"\bexec\s*\(",
        r"\beval\s*\(",
        r"\b__import__\s*\(",
        r"compile\s*\(.*exec",
        r"globals\(\)\[",
        r"getattr\s*\(.*__",
    ],
    "encoding_obfuscation": [
        r"\bbase64\b",
        r"\\x[0-9a-fA-F]{2}",     # hex-escape sequences
        r"\\u[0-9a-fA-F]{4}",     # unicode escapes в подозрительном контексте
        r"atob\s*\(",
        r"btoa\s*\(",
        r"rot13",
        r"chr\s*\(\s*\d+\s*\)\s*\+",  # chr() конкатенация — типичный обфускатор
    ],
}

# Серьёзность по категории
SEVERITY = {
    "prompt_injection": "HIGH",
    "data_exfiltration": "HIGH",
    "code_execution": "HIGH",
    "network_calls": "MEDIUM",
    "encoding_obfuscation": "MEDIUM",
}

# ─── Логирование ──────────────────────────────────────────────────────────────

def setup_logger():
    logger = logging.getLogger("scanner")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)
    return logger

logger = setup_logger()

# ─── Сканер ───────────────────────────────────────────────────────────────────

class SecurityScanner:

    def scan_content(self, content: str) -> dict:
        """
        Сканирует текст на угрозы.
        Возвращает: {"safe": bool, "findings": [...], "max_severity": str}
        """
        findings = []
        content_lower = content.lower()

        for category, patterns in THREAT_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    findings.append({
                        "category": category,
                        "severity": SEVERITY[category],
                        "pattern": pattern,
                        "matches": matches[:3],  # первые 3 совпадения
                    })

        max_severity = "NONE"
        if any(f["severity"] == "HIGH" for f in findings):
            max_severity = "HIGH"
        elif any(f["severity"] == "MEDIUM" for f in findings):
            max_severity = "MEDIUM"

        return {
            "safe": max_severity not in ("HIGH",),
            "findings": findings,
            "max_severity": max_severity,
        }

    def scan_skill(self, skill_dir: Path) -> dict:
        """
        Сканирует все .md файлы в папке skill.
        """
        skill_name = skill_dir.name
        all_findings = []

        # Читаем SKILL.md и все .md файлы
        md_files = list(skill_dir.rglob("*.md"))
        if not md_files:
            logger.warning(f"[{skill_name}] Нет .md файлов — пропускаем")
            return {"skill": skill_name, "safe": True, "findings": [], "max_severity": "NONE"}

        combined_content = ""
        for md_file in md_files:
            try:
                combined_content += md_file.read_text(encoding="utf-8", errors="ignore")
                combined_content += "\n\n"
            except Exception as e:
                logger.warning(f"[{skill_name}] Не удалось прочитать {md_file.name}: {e}")

        result = self.scan_content(combined_content)
        result["skill"] = skill_name
        result["files_scanned"] = [f.name for f in md_files]

        return result

    def process_incoming(self) -> list:
        """
        Обрабатывает все skills в incoming-skills/.
        Опасные → quarantine, безопасные → возвращает список для следующего шага.
        """
        if not INCOMING_DIR.exists():
            logger.error(f"Папка {INCOMING_DIR} не найдена")
            return []

        skill_dirs = [d for d in INCOMING_DIR.iterdir() if d.is_dir()]
        if not skill_dirs:
            logger.info("incoming-skills/ пустая — нечего сканировать")
            return []

        approved = []
        logger.info(f"\n{'='*60}")
        logger.info(f"REGEX SCANNER — начало проверки {len(skill_dirs)} skills")
        logger.info(f"{'='*60}")

        for skill_dir in sorted(skill_dirs):
            result = self.scan_skill(skill_dir)
            skill_name = result["skill"]

            if result["max_severity"] == "HIGH":
                # Перемещаем в карантин
                dest = QUARANTINE_DIR / skill_name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(skill_dir), str(dest))

                categories = list({f["category"] for f in result["findings"]})
                logger.info(
                    f"QUARANTINE | {skill_name} | "
                    f"severity={result['max_severity']} | "
                    f"threats={categories}"
                )
            else:
                # Передаём дальше
                approved.append({
                    "path": skill_dir,
                    "name": skill_name,
                    "scan_result": result,
                })

                status = "CLEAN" if result["max_severity"] == "NONE" else "WARN"
                logger.info(
                    f"{status}     | {skill_name} | "
                    f"severity={result['max_severity']} | "
                    f"findings={len(result['findings'])}"
                )

        logger.info(f"\nРезультат regex-сканирования: {len(approved)}/{len(skill_dirs)} прошли")
        return approved


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    scanner = SecurityScanner()
    approved = scanner.process_incoming()

    print(f"\n✓ Прошли regex-проверку: {len(approved)} skills")
    for item in approved:
        severity = item["scan_result"]["max_severity"]
        flag = "⚠" if severity == "MEDIUM" else "✓"
        print(f"  {flag} {item['name']} (severity: {severity})")
