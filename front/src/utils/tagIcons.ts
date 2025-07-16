export const getTagIcon = (tag: string): string => {
  const iconMap: Record<string, string> = {
    frontend: 'mdi-monitor-dashboard',
    backend: 'mdi-server',
    urgent: 'mdi-alert-circle',
    api: 'mdi-api',
    database: 'mdi-database',
    ui: 'mdi-palette',
    ux: 'mdi-account-group',
    testing: 'mdi-test-tube',
    security: 'mdi-shield-check'
  }

  return iconMap[tag.toLowerCase()] || 'mdi-tag'
}