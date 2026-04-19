// Use the same host as the Next app (e.g. localhost, not 127.0.0.1) so refresh cookies work with SameSite=Lax.
const raw =
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

/** JSON API base URL with trailing slash (matches RTK `baseApi`). */
export const API_BASE_URL = raw.endsWith("/") ? raw : `${raw}/`;
