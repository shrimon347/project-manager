"use client";

import { AuthSessionProvider } from "@/app/(app)/auth-session-provider";
import { Footer } from "@/components/dashboard/footer";
import { Sidebar } from "@/components/dashboard/sidebar";
import { cn } from "@/lib/utils";

import { useAppSelector } from "@/store/hooks";
import { selectSidebarOpenState } from "@/store/selectors/sidebarSelectors";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const settings = useAppSelector((state) => state.sidebar.settings);
    const openState = useAppSelector(selectSidebarOpenState);

    return (
        <>
            <Sidebar />

            <main
                className={cn(
                    "min-h-[calc(100vh-56px)] bg-zinc-50 dark:bg-zinc-900 transition-[margin-left] ease-in-out duration-300",
                    !settings.disabled &&
                        (!openState ? "lg:ml-[90px]" : "lg:ml-72"),
                )}
            >
                <AuthSessionProvider>{children}</AuthSessionProvider>
            </main>

            <footer
                className={cn(
                    "transition-[margin-left] ease-in-out duration-300",
                    !settings.disabled &&
                        (!openState ? "lg:ml-[90px]" : "lg:ml-72"),
                )}
            >
                <Footer />
            </footer>
        </>
    );
}
