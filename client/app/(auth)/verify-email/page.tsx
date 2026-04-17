import { Suspense } from "react";

import { VerifyEmailHandler } from "../../../components/auth/verify-email-handler";

export default function VerifyEmailPage() {
    return (
        <div className="flex min-h-svh flex-col items-center justify-center p-6">
            <Suspense
                fallback={
                    <p className="text-muted-foreground text-sm">Loading…</p>
                }
            >
                <VerifyEmailHandler />
            </Suspense>
        </div>
    );
}
