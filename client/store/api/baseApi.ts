import type { RootState } from "@/store";
import { loggedOut, setAccessToken } from "@/store/slices/authSlice";
import {
    BaseQueryFn,
    FetchArgs,
    FetchBaseQueryError,
    createApi,
    fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";

import { API_BASE_URL } from "@/lib/api-base-url";
import { TokenRefreshResponseData } from "../types/auth.types";

/**
 * Base query with credentials + auth header
 */
const rawBaseQuery = fetchBaseQuery({
    baseUrl: API_BASE_URL,
    credentials: "include",
    prepareHeaders: (headers, { getState }) => {
        const token = (getState() as RootState).auth.accessToken;
        if (token) {
            headers.set("authorization", `Bearer ${token}`);
        }
        return headers;
    },
});

/**
 * Base query with automatic re-auth (refresh token)
 */
const baseQueryWithReauth: BaseQueryFn<
    string | FetchArgs,
    unknown,
    FetchBaseQueryError
> = async (args, api, extraOptions) => {
    let result = await rawBaseQuery(args, api, extraOptions);

    // Normalize URL/path for endpoint checks
    const rawUrl = typeof args === "string" ? args : (args.url ?? "");
    const url = rawUrl.toLowerCase().replace(/^\/+/, "");

    // Skip refresh for these endpoints
    const shouldSkipRefresh =
        /(^|\/)auth\/login\/?($|\?)/.test(url) ||
        /(^|\/)auth\/logout\/?($|\?)/.test(url) ||
        /(^|\/)auth\/refresh\/?($|\?)/.test(url);

    // Only attempt refresh if we still have an access token in state.
    // This prevents post-logout 401s from triggering a doomed refresh call.
    const hasAccessToken = Boolean(
        (api.getState() as RootState).auth.accessToken,
    );

    // Prevent infinite retry loop
    const isRetry =
        typeof args !== "string" &&
        args.headers &&
        (args.headers as Record<string, string>)["x-retry"] === "true";

    if (
        result.error?.status === 401 &&
        hasAccessToken &&
        !shouldSkipRefresh &&
        !isRetry
    ) {
        // Try refresh token
        const refreshResult = await rawBaseQuery(
            {
                url: "auth/refresh/",
                method: "POST",
                credentials: "include", // ensure cookie is sent
            },
            api,
            extraOptions,
        );

        if (refreshResult.data) {
            const newAccessToken = (
                refreshResult.data as TokenRefreshResponseData
            )?.access;

            if (newAccessToken) {
                // Save new access token
                api.dispatch(setAccessToken(newAccessToken));

                // Retry original request ONCE
                result = await rawBaseQuery(
                    typeof args === "string"
                        ? args
                        : {
                              ...args,
                              headers: {
                                  ...(args.headers || {}),
                                  "x-retry": "true",
                              },
                          },
                    api,
                    extraOptions,
                );
            } else {
                // No token → logout
                api.dispatch(loggedOut());
            }
        } else {
            // Refresh failed → logout
            api.dispatch(loggedOut());
        }
    }

    return result;
};

/**
 * API instance
 */
export const baseApi = createApi({
    reducerPath: "api",
    baseQuery: baseQueryWithReauth,
    tagTypes: ["User"],
    endpoints: () => ({}),
});
