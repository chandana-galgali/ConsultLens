// Shape copied from the real care_ai_vision_fe manifest (github.com/ohcnetwork/care_ai_vision_fe, src/manifest.tsx).
// The scaffold generates its own manifest.tsx - keep ITS structure and just add the entries below.
import { lazy } from "react";

import routes from "./routes";

const manifest = {
  plugin: "care_consultlens_fe",
  routes,
  extends: [],
  components: {
    // TODO: care_fe's src/pluginTypes.ts lists the named slots/tabs a plugin may fill (e.g. a patient-page tab).
    // Add the one for the patient page there once confirmed, pointing at ConsultLensPage.
  },
  userNavItems: [],
  devices: [],
} as const;

export default manifest;

export const ConsultLensPage = lazy(() => import("./components/ConsultLensPage"));
