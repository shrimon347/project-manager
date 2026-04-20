import { Navbar } from "@/components/dashboard/navbar";

interface ContentLayoutProps {
    title: string;
    children: React.ReactNode;
    header?: React.ReactNode;
}

export function ContentLayout({ title, header, children }: ContentLayoutProps) {
    return (
        <div>
            <Navbar title={title} />
            <div className="container pt-8 pb-8 px-4 sm:px-8">
                {header && <div className="mb-6">{header}</div>}
                {children}
            </div>
        </div>
    );
}
