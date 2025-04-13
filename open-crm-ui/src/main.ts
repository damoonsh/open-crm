import { createApp, provide, h } from "vue";
import { DefaultApolloClient } from "@vue/apollo-composable";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import router from "./router";
import App from "./App.vue";
import { apolloClient } from "./plugins/apollo";

import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";
import "./style.css";

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    themes: {
      light: {
        colors: {
          primary: "#1867C0",
          secondary: "#5CBBF6",
          accent: "#4CAF50",
          logout: "#ff5252", // Custom color for logout button
        },
      },
      dark: {
        colors: {
          primary: "#2196F3",
          secondary: "#424242",
          accent: "#FF4081",
          logout: "#ff7676", // Lighter shade for dark mode
        },
      },
    },
  },
});

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp({
  setup() {
    provide(DefaultApolloClient, apolloClient);
  },
  render: () => h(App),
});

app.use(pinia);
app.use(vuetify);
app.use(router);
app.mount("#app");
