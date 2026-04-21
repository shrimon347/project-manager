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

let refreshPromise: Promise<string | null> | null = null;

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

    // Prevent infinite retry loop
    const isRetry =
        typeof args !== "string" &&
        args.headers &&
        (args.headers as Record<string, string>)["x-retry"] === "true";

    if (result.error?.status === 401 && !shouldSkipRefresh && !isRetry) {
        if (!refreshPromise) {
            refreshPromise = (async () => {
                const refreshResult = await rawBaseQuery(
                    {
                        url: "auth/refresh/",
                        method: "POST",
                        credentials: "include",
                    },
                    api,
                    extraOptions,
                );

                const newAccessToken = (
                    refreshResult.data as TokenRefreshResponseData | undefined
                )?.access;

                if (newAccessToken) {
                    api.dispatch(setAccessToken(newAccessToken));
                    return newAccessToken;
                }

                return null;
            })().finally(() => {
                refreshPromise = null;
            });
        }

        const refreshedAccessToken = await refreshPromise;

        if (refreshedAccessToken) {
            // Retry original request ONCE after the shared refresh completes.
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
    tagTypes: ["User", "Workspace"],
    endpoints: () => ({}),
});
