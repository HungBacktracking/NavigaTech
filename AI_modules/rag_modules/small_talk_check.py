import re
from typing import List


class AdvancedRuleBasedSmallTalkChecker:
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.rule_patterns: List[(re.Pattern, int)] = [
            (re.compile(r'\b(hi|hello|hey|good (morning|afternoon|evening))\b', re.I), 3),
            (re.compile(r'\b(bye|goodbye|see you|farewell)\b', re.I), 3),
            (re.compile(r'\b(how are you|how\'s it going|what\'s up)\b', re.I), 3),
            (re.compile(r'\b(joke|funny|laugh)\b', re.I), 4),
            (re.compile(r'\b(thanks?|thank you|appreciate)\b', re.I), 2),
            (re.compile(r'\b(weather|time|weekend|holiday)\b', re.I), 1),
            (re.compile(r"\b(i('m| am)|my name is|this is|call me)\b", re.I), 3),
        ]

        self.fallback_classifier = None

    def normalize(self, text: str) -> str:

        return re.sub(r'[^\w\s\']', ' ', text.lower()).strip()

    def is_small_talk(self, text: str) -> bool:
        norm = self.normalize(text)
        score = 0
        for pattern, weight in self.rule_patterns:
            if pattern.search(norm):
                score += weight

        if 0 < score < self.threshold and self.fallback_classifier:
            return self.fallback_classifier(norm)
        return score >= self.threshold
