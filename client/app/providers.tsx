"use client";

import { ThemeProvider } from "next-themes";
import { Provider } from "react-redux";

import { Toaster } from "@/components/ui/sonner";
import { store } from "@/store";

type ProvidersProps = {
    children: React.ReactNode;
};

export function Providers({ children }: ProvidersProps) {
    return (
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
        >
            <Provider store={store}>
                {children}
                <Toaster position="top-center" />
            </Provider>
        </ThemeProvider>
    );
}
