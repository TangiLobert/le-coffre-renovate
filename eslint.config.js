import createConfigForNuxt from '@nuxt/eslint-config'
import stylistic from '@stylistic/eslint-plugin'

export default createConfigForNuxt({
  features: {
    stylistic: stylistic.configs.recommended,
  },
  ignores: [
    'server/database/migrations/*',
  ],
})
  .override('nuxt/javascript',
    {
      rules: {
        'quotes': ['warn', 'single', { avoidEscape: true }],
        'eqeqeq': ['warn', 'always', { null: 'never' }],
        'no-debugger': ['error'],
        'no-console': 'off',
        'no-empty': ['warn', { allowEmptyCatch: true }],
        'no-process-exit': 'off',
        'no-useless-escape': 'off',
        'prefer-const': [
          'warn',
          {
            destructuring: 'all',
          },
        ],
        'no-unused-vars': [
          'warn',
          {
            argsIgnorePattern: '^_',
            varsIgnorePattern: '^_',
            ignoreRestSiblings: true,
          },
        ],
        'vue/max-attributes-per-line': ['error', {
          singleline: {
            max: 3,
          },
          multiline: {
            max: 1,
          },
        }],
      },
    },
  )
