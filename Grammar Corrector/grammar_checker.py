import spacy


# ============================================================
# LOAD SPACY
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def third_person_singular(verb):
    """
    Convert a base verb to third-person singular.

    Examples:
        go     -> goes
        study  -> studies
        watch  -> watches
        play   -> plays
    """

    verb = verb.lower()

    irregular = {
        "go": "goes",
        "do": "does",
        "have": "has",
        "be": "is",
    }

    if verb in irregular:
        return irregular[verb]

    # study -> studies
    if verb.endswith("y") and len(verb) > 1:
        if verb[-2] not in "aeiou":
            return verb[:-1] + "ies"

    # watch -> watches
    # wash  -> washes
    # fix   -> fixes
    # pass  -> passes
    # go    -> goes
    if verb.endswith(("s", "x", "z", "ch", "sh", "o")):
        return verb + "es"

    # play -> plays
    # walk -> walks
    # work -> works
    return verb + "s"


def base_form(verb):
    """
    Convert common third-person singular forms back to base form.

    Examples:
        walks   -> walk
        studies -> study
        watches -> watch
        goes    -> go
    """

    verb = verb.lower()

    irregular = {
        "does": "do",
        "has": "have",
        "is": "be",
    }

    if verb in irregular:
        return irregular[verb]

    if verb.endswith("ies") and len(verb) > 3:
        return verb[:-3] + "y"

    if verb.endswith(("ches", "shes", "xes", "zes", "oes")):
        return verb[:-2]

    if verb.endswith("s") and not verb.endswith("ss"):
        return verb[:-1]

    return verb


# ============================================================
# FIND SUBJECT
# ============================================================

def find_subject(doc, token_index):
    """
    Try to find the grammatical subject of a verb.

    First uses spaCy dependency parsing.
    If that does not work, falls back to nearby words.
    """

    token = doc[token_index]

    # --------------------------------------------------------
    # First: spaCy dependency parsing
    # --------------------------------------------------------

    for child in token.children:

        if child.dep_ in ("nsubj", "nsubjpass"):

            subject_word = child.text.lower()

            if subject_word in (
                "i",
                "you",
                "we",
                "they",
                "he",
                "she",
                "it",
            ):
                return child

    # --------------------------------------------------------
    # Second: search previous tokens
    # --------------------------------------------------------

    subjects = {
        "i",
        "you",
        "we",
        "they",
        "he",
        "she",
        "it",
    }

    # Look back up to 5 words
    start = max(0, token_index - 5)

    for i in range(token_index - 1, start - 1, -1):

        word = doc[i].text.lower()

        if word in subjects:
            return doc[i]

    return None


# ============================================================
# GRAMMAR CHECKER
# ============================================================

def check_grammar(text):

    doc = nlp(text)

    errors = []

    for token in doc:

        word = token.text.lower()

        # We only care about verbs and auxiliaries
        if token.pos_ not in ("VERB", "AUX"):
            continue

        subject = find_subject(doc, token.i)

        if subject is None:
            continue

        subject_word = subject.text.lower()

        # ====================================================
        # HE / SHE / IT
        # ====================================================

        if subject_word in ("he", "she", "it"):

            # -----------------------------------------------
            # have -> has
            # -----------------------------------------------

            if word == "have":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "has",
                    "message": (
                        f"Use 'has' with '{subject_word}'."
                    )
                })

            # -----------------------------------------------
            # are -> is
            # -----------------------------------------------

            elif word == "are":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "is",
                    "message": (
                        f"Use 'is' with '{subject_word}'."
                    )
                })

            # -----------------------------------------------
            # Base verb
            #
            # He go -> He goes
            # She walk -> She walks
            # She study -> She studies
            # -----------------------------------------------

            elif (
                token.pos_ == "VERB"
                and token.tag_ in ("VB", "VBP")
                and word not in ("be", "do", "have")
            ):

                suggestion = third_person_singular(word)

                if suggestion != word:

                    errors.append({
                        "index": token.i,
                        "error": token.text,
                        "suggestion": suggestion,
                        "message": (
                            f"Use '{suggestion}' with "
                            f"'{subject_word}'."
                        )
                    })

        # ====================================================
        # I
        # ====================================================

        elif subject_word == "i":

            # -----------------------------------------------
            # is -> am
            # -----------------------------------------------

            if word == "is":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "am",
                    "message": "Use 'am' with 'I'."
                })

            # -----------------------------------------------
            # has -> have
            # -----------------------------------------------

            elif word == "has":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "have",
                    "message": "Use 'have' with 'I'."
                })

        # ====================================================
        # YOU / WE / THEY
        # ====================================================

        elif subject_word in ("you", "we", "they"):

            # -----------------------------------------------
            # has -> have
            # -----------------------------------------------

            if word == "has":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "have",
                    "message": (
                        f"Use 'have' with '{subject_word}'."
                    )
                })

            # -----------------------------------------------
            # is -> are
            # -----------------------------------------------

            elif word == "is":

                errors.append({
                    "index": token.i,
                    "error": token.text,
                    "suggestion": "are",
                    "message": (
                        f"Use 'are' with '{subject_word}'."
                    )
                })

            # -----------------------------------------------
            # Third-person verb -> base verb
            #
            # They walks -> They walk
            # They studies -> They study
            # -----------------------------------------------

            elif (
                token.pos_ == "VERB"
                and token.tag_ == "VBZ"
            ):

                suggestion = base_form(word)

                if suggestion != word:

                    errors.append({
                        "index": token.i,
                        "error": token.text,
                        "suggestion": suggestion,
                        "message": (
                            f"Use '{suggestion}' with "
                            f"'{subject_word}'."
                        )
                    })

    return errors, doc


# ============================================================
# CORRECT TEXT
# ============================================================

def correct_text(text, errors=None):

    doc = nlp(text)

    replacements = {}

    if errors:

        for error in errors:

            replacements[
                error["index"]
            ] = error["suggestion"]

    result = ""

    for token in doc:

        replacement = replacements.get(
            token.i,
            token.text
        )

        # Preserve capitalization
        if (
            replacement
            and token.text
            and token.text[0].isupper()
        ):
            replacement = replacement.capitalize()

        result += replacement

        # Preserve spaces and punctuation
        result += token.whitespace_

    return result