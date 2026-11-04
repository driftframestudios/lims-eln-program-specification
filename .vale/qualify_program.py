"""Exercise the optional Program authoring cues and their profile boundary."""

from pathlib import Path

from qualify import qualify


ROOT = Path(__file__).resolve().parents[1]
COUNT = "ProgramReview.CountToConclusion"
WORDING = "ProgramReview.ContextualWording"
CLAIM = "We inventoried all 17 observations, so the comparison is complete."

CASES = {
    "review-claim.md": (
        CLAIM + "\n\n"
        "Of the 17 observations, 10 agree, four have explained variation and three "
        "differ. The scientific reviewer compares the analyte, value and unit "
        "for the three differences before deciding whether the methods agree.\n\n"
        "We counted 17 laboratory\nobservations, so the study is ready.\n\n"
        "All three differences were resolved.\n\n"
        "We reviewed 17 fields, so the methods are equivalent.\n\n"
        "We reviewed all 17 fields, establishing measurement equivalence.\n\n"
        "We reviewed all 17 fields, establishing which fields had missing units.",
        [(line, COUNT, "suggestion") for line in (1, 5, 10, 12)],
    ),
    "selected-context.md": (
        "The collaboration seams are visible.\n\n"
        "The next decision moves need an owner.\n\n"
        "The evidence arrives.\n\n"
        "The review rooms are open.\n\n"
        "The proposal covers the decision surfaces.\n\n"
        "The review instrument needs a name.\n\n"
        "The load-bearing assumption still holds.\n\n"
        "Name the owner of the seam.\n\n"
        "Name the owner of the specimen record. Inspect the welded seam.",
        [(line, WORDING, "suggestion") for line in (1, 3, 5, 7, 9, 11, 13, 15)],
    ),
    "laboratory-language.md": (
        "The review room houses a biosafety cabinet.\n\n"
        "The instrument sent the result to two rooms. The specimen moves between "
        "clean surfaces. A message arrives with a sealed seam.\n\n"
        "`instrument_id` identifies the instrument.\n\n"
        "> The evidence arrives in a review room.\n\n"
        "```json\n{\"decision surface\": \"load-bearing\"}\n```\n\n"
        "Keep `load-bearing` as the quoted schema value.",
        [(1, WORDING, "suggestion")],
    ),
}

SHARED_ONLY = {
    "ordinary-profile.md": (
        CLAIM + "\n\nThe coordination seam is visible.\n\nClearly the report is ready.",
        [(5, "SiteReading.EvidenceGrounding", "suggestion")],
    ),
}


if __name__ == "__main__":
    qualify(ROOT / ".vale" / "program.ini", CASES)
    qualify(ROOT / ".vale.ini", SHARED_ONLY)
    print("Qualified the Program suggestions and their opt-in Markdown profile.")
