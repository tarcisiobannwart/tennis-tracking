import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpApi from 'i18next-http-backend';

import ptBR from './locales/pt-BR.json';
import enUS from './locales/en-US.json';

const resources = {
  'pt-BR': {
    translation: ptBR
  },
  'en-US': {
    translation: enUS
  }
};

i18n
  .use(HttpApi)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'pt-BR', // Idioma padrão: Português
    fallbackLng: 'pt-BR',
    debug: false,

    interpolation: {
      escapeValue: false // React já faz o escape
    },

    detection: {
      order: ['localStorage', 'cookie', 'navigator', 'htmlTag'],
      caches: ['localStorage', 'cookie'],
    }
  });

export default i18n;