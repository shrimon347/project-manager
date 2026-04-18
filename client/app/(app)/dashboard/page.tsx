"use client";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/store/hooks";

export default function DashboardPage() {
    const { logout, isLoggingOut } = useAuth();

    return (
        <main className="p-6">
            <div className="flex items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold">Dashboard</h1>
                    <p className="mt-2 text-sm text-muted-foreground">
                        You are authenticated and can access protected routes.
                    </p>
                </div>
                <Button
                    type="button"
                    variant="outline"
                    onClick={() => void logout()}
                    disabled={isLoggingOut}
                >
                    {isLoggingOut ? "Signing out..." : "Logout"}
                </Button>
            </div>
        </main>
    );
}
