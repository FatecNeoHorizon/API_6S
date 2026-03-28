module.exports = {
  extends: ["@commitlint/config-conventional"],
  plugins: [
    {
      rules: {
        "footer-issue-reference": ({ footer }) => {
          const hasRef = /(?:Closes|Ref:)?\s*#\d+/.test(footer ?? "");
          return [
            hasRef,
            "Footer must include an issue reference: #123, Closes #123, or Ref: #123"
          ];
        }
      }
    }
  ],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "chore",
        "ci",
        "revert"
      ]
    ],
    "type-case": [2, "always", "lowercase"],
    "type-empty": [2, "never"],
    "scope-case": [2, "always", "lowercase"],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "subject-case": [2, "always", "lower-case"],
    "header-max-length": [2, "always", 1000],
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"],
    "footer-issue-reference": [2, "always"]
  },
  helpURL: "https://www.conventionalcommits.org/"
};