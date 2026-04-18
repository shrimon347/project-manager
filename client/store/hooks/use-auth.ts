"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { useLogoutMutation } from "@/store/api/authApi";
import { loggedOut } from "@/store/slices/authSlice";
import { useAppDispatch, useAppSelector } from "@/store/hooks/redux-hooks";
import { getApiErrorMessage } from "@/lib/api-error";

export function useAuth() {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const [logoutApi, { isLoading: isLoggingOut }] = useLogoutMutation();

    const logout = useCallback(async () => {
        try {
            await logoutApi().unwrap();
        } catch (error) {
            // We still clear client session if backend token is already invalid.
            const message = getApiErrorMessage(error, {
                fallback: "Logout failed. Please try again.",
            });
            console.error(message);
        } finally {
            dispatch(loggedOut());
            router.replace("/login");
        }
    }, [dispatch, logoutApi, router]);

    return {
        isAuthenticated: Boolean(accessToken),
        accessToken,
        logout,
        isLoggingOut,
    };
}
