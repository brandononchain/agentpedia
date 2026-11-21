import build_index


def catalog():
    return {
        "repoUrl": "https://github.com/brandononchain/agentpedia",
        "stats": {
            "skills": 97,
            "agents": 21,
            "categories": 23,
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "clean": 97,
        },
        "audit": {
            "graceDays": 14,
            "stats": {
                "onHold": 0,
                "grades": {"A": 118, "B": 0, "C": 0, "D": 0, "F": 0},
            },
        },
        "drops": [{"date": "2026-11-21", "skills": ["agentpedia-submit"], "agents": []}],
    }


def certs():
    return {"listed": 116, "verified": 2, "certified": 0}


def test_badges_and_table_use_the_given_counts():
    badges = build_index.render_badges(catalog(), certs())
    table = build_index.render_stats_table(catalog(), certs())
    assert "skills-97-" in badges
    assert "agents-21-" in badges
    assert "shelves-23-" in badges
    assert "all_100,_0_errors" in badges
    assert "audit-118_A-" in badges
    assert "listed-116-" in badges
    assert "verified-2-" in badges
    assert "certified-0-" in badges
    assert "on_hold-0-" in badges
    assert "latest_drop-2026--11--21-" in badges
    assert "license-Apache--2.0-" in badges
    assert "site-agentpedia.sh-" in badges
    assert "96" not in badges
    assert "| Skills | 97 |" in table
    assert "| Agents | 21 |" in table
    assert "| Shelves | 23 |" in table
    assert "| Listed | 116 |" in table
    assert "| Verified | 2 |" in table
    assert "| Certified | 0 |" in table
    assert "| On hold | 0 |" in table
    assert "| Latest drop | 2026-11-21 |" in table
    assert "96" not in table


def test_lint_badge_does_not_claim_100_when_the_catalog_does_not():
    data = catalog()
    data["stats"]["clean"] = 90
    data["stats"]["errors"] = 2
    badges = build_index.render_badges(data, certs())
    assert "all_100" not in badges
    assert "2_errors" in badges


def test_vetting_uses_the_grace_period_it_is_given():
    text = build_index.render_vetting(14)
    assert "14-day" in text
    assert "scores 100" in text
    assert "grade F" in text
    assert "critical finding" in text
    assert "Verified" in text
    assert "Certified" in text


def test_marked_regions_are_replaced_without_touching_the_rest():
    original = "Keep this.\n<!-- stats:start -->\nold\n<!-- stats:end -->\nAnd this.\n"
    updated = build_index.replace_marked(original, "stats", "| Skills | 97 |")
    assert updated.startswith("Keep this.\n")
    assert updated.endswith("And this.\n")
    assert "| Skills | 97 |" in updated
    assert "old" not in updated
