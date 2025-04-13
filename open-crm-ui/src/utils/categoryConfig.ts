export interface CategoryConfig {
  icon: string;
  color: string;
}

export const categoryConfigs: Record<string, CategoryConfig> = {
  Development: { icon: 'mdi-code-braces', color: 'indigo' },
  Testing: { icon: 'mdi-test-tube', color: 'teal' },
  Documentation: { icon: 'mdi-file-document', color: 'blue' },
  Meeting: { icon: 'mdi-account-group', color: 'purple' },
  'Bug Fix': { icon: 'mdi-bug', color: 'red' },
  Design: { icon: 'mdi-palette', color: 'pink' },
  Research: { icon: 'mdi-magnify', color: 'orange' }
}