// Conventional Commits validation config, used by the "Conventional Commits"
// GitHub Actions workflow (wagoid/commitlint-github-action). There is no need
// to install Node.js or commitlint locally — validation happens in CI.
export default {
  extends: ['@commitlint/config-conventional'],
  // Release Please's squash commits ("chore(main): release 0.1.0") use the
  // branch name as their scope, which is not in the scope list below.
  ignores: [(message) => /^chore\(main\): release /.test(message)],
  rules: {
    // Keep in sync with the scopes in AGENTS.md, CONTRIBUTING.md and
    // .github/workflows/commitlint.yml. A scope is optional.
    'scope-enum': [2, 'always', ['ds', 'algo', 'bench', 'ci', 'release', 'docs', 'deps', 'repo']],
    // PRs are squash-merged with the PR body as the commit body; PR bodies
    // routinely exceed 100-character lines, so don't fail on body length.
    'body-max-line-length': [0, 'always', 100],
    'footer-max-line-length': [0, 'always', 100],
  },
};
