import type { AuthState } from "@/store/types/auth.types";
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

const ACCESS_TOKEN_KEY = "pm_access_token";

function readStoredAccessToken(): string | null {
    if (typeof window === "undefined") {
        return null;
    }
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

function persistAccessToken(token: string | null) {
    if (typeof window === "undefined") {
        return;
    }
    if (token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        return;
    }
    localStorage.removeItem(ACCESS_TOKEN_KEY);
}

const initialState: AuthState = {
    accessToken: readStoredAccessToken(),
};

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setAccessToken: (state, action: PayloadAction<string>) => {
            state.accessToken = action.payload;
            persistAccessToken(action.payload);
        },
        loggedOut: (state) => {
            state.accessToken = null;
            persistAccessToken(null);
        },
    },
});

export const { setAccessToken, loggedOut } = authSlice.actions;
export default authSlice.reducer;
