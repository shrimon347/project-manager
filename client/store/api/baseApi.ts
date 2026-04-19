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

    // Normalize URL
    const url = typeof args === "string" ? args : (args.url ?? "");

    // 🚫 Skip refresh for these endpoints
    const shouldSkipRefresh =
        url.includes("auth/login") ||
        url.includes("auth/logout") ||
        url.includes("auth/refresh");

    // Prevent infinite retry loop
    const isRetry =
        typeof args !== "string" &&
        args.headers &&
        (args.headers as Record<string, string>)["x-retry"] === "true";

    if (result.error?.status === 401 && !shouldSkipRefresh && !isRetry) {
        // 🔁 Try refresh token
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
            const newAccessToken = (refreshResult.data as TokenRefreshResponseData)?.access;

            if (newAccessToken) {
                // Save new access token
                api.dispatch(setAccessToken(newAccessToken));

                // 🔁 Retry original request ONCE
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
