"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import DashboardLayout from "@/components/dashboard/dashboardLayout";
import { useGetMeQuery } from "@/store/api/authApi";
import { useAppSelector } from "@/store/hooks";

type AppLayoutProps = {
    children: React.ReactNode;
};

export default function AppLayout({ children }: AppLayoutProps) {
    const router = useRouter();
    const accessToken = useAppSelector((state) => state.auth.accessToken);
    const { isLoading, isFetching } = useGetMeQuery();

    const isChecking = isLoading || isFetching;

    useEffect(() => {
        if (isChecking) {
            return;
        }

        if (!accessToken) {
            router.replace("/login");
        }
    }, [accessToken, isChecking, router]);

    if (isChecking) {
        return (
            <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
                Checking session...
            </div>
        );
    }

    if (!accessToken) {
        return (
            <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
                Redirecting to login...
            </div>
        );
    }

    return <DashboardLayout>{children}</DashboardLayout>;
}
