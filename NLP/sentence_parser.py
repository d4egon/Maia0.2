class SentenceParser:
    def parse(self, tokens):
        parsed = {"subject": None, "action": None, "object": None}

        if "you" in tokens and "are" in tokens:
            parsed["subject"] = "you"
            parsed["action"] = "are"
            parsed["object"] = tokens[-1]  # Assume last word as object

        return parsed