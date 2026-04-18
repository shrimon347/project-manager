"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useRefreshTokenMutation } from "@/store/api/authApi";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { loggedOut } from "@/store/slices/authSlice";

type AppLayoutProps = {
    children: React.ReactNode;
};

export default function AppLayout({ children }: AppLayoutProps) {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const [refreshToken] = useRefreshTokenMutation();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        let isMounted = true;

        const verifySession = async () => {
            if (accessToken) {
                if (isMounted) {
                    setIsChecking(false);
                }
                return;
            }

            try {
                await refreshToken().unwrap();
            } catch {
                dispatch(loggedOut());
                router.replace("/login");
            } finally {
                if (isMounted) {
                    setIsChecking(false);
                }
            }
        };

        void verifySession();
        return () => {
            isMounted = false;
        };
    }, [accessToken, dispatch, refreshToken, router]);

    if (isChecking) {
        return (
            <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
                Checking session...
            </div>
        );
    }

    if (!accessToken) {
        return null;
    }

    return children;
}
