import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { API_BASE_URL } from "@/lib/api-base-url";

export const baseApi = createApi({
    reducerPath: "api",

    baseQuery: fetchBaseQuery({
        baseUrl: API_BASE_URL,
    }),

    endpoints: () => ({}), // empty, we inject later
});
