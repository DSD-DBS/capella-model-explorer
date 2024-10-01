/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./src/**/*.{html,js,jsx}'],
  theme: {
    extend: {
      screens: {
        'custom-phone-width': '512px',
        '3xl': '1800px'
      },
      boxShadow: {
        white: '0 0 15px rgba(255, 255, 255, 0.1)',
        dark: '0 4px 6px 0 rgba(0, 0, 0, 0.2)'
      },
      animation: {
        'spin-slow': 'spin 1.6s linear infinite'
      },
      opacity: {
        54: '.54'
      },
      colors: {
        'custom-light': '#dee4e7',
        'custom-dark-1': '#121212',
        'custom-dark-2': '#282828',
        'custom-dark-3': '#3f3f3f',
        'custom-dark-4': '#575757',
        'custom-dark-error': '#ed8796',
        'custom-blue': '#2196f3',
        'custom-blue-hover': '#0b5ea1'
      }
    }
  },
  plugins: ['tailwind-scrollbar']
};
