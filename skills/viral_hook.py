"""Viral hook scoring."""
class ViralHookAnalyzer:
    """Score short-form hooks with transparent heuristics."""
    def score(self, text: str) -> dict:
        """Return hook score, risks, and rewrites."""
        score=5 + int('you' in text.lower()) + int('?' in text) + int(len(text.split())<18)
        return {'score':min(score,10),'risks':['Add a pattern interrupt in first five seconds'] if score<7 else [],'alternatives':[f'You will not believe this: {text[:80]}', f'Stop scrolling — {text[:80]}', f'I tested this so you do not have to: {text[:80]}']}
