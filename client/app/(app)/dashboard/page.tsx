"use client";

import { ContentLayout } from "@/components/dashboard/content-layout";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import Link from "next/link";

import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { setSettings } from "@/store/slices/sidebarSlice";

export default function DashboardPage() {
    const dispatch = useAppDispatch();

    const settings = useAppSelector((state) => state.sidebar.settings);

    return (
        <ContentLayout title="Dashboard">
            <Breadcrumb>
                <BreadcrumbList>
                    <BreadcrumbItem>
                        <BreadcrumbLink asChild>
                            <Link href="/">Home</Link>
                        </BreadcrumbLink>
                    </BreadcrumbItem>

                    <BreadcrumbSeparator />

                    <BreadcrumbItem>
                        <BreadcrumbPage>Dashboard</BreadcrumbPage>
                    </BreadcrumbItem>
                </BreadcrumbList>
            </Breadcrumb>

            <TooltipProvider>
                <div className="flex gap-6 mt-6">
                    {/* Hover Open */}
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center space-x-2">
                                <Switch
                                    id="is-hover-open"
                                    checked={settings.isHoverOpen}
                                    onCheckedChange={(value) =>
                                        dispatch(
                                            setSettings({ isHoverOpen: value }),
                                        )
                                    }
                                />
                                <Label htmlFor="is-hover-open">
                                    Hover Open
                                </Label>
                            </div>
                        </TooltipTrigger>

                        <TooltipContent>
                            <p>
                                When hovering on the sidebar in mini state, it
                                will open
                            </p>
                        </TooltipContent>
                    </Tooltip>

                    {/* Disable Sidebar */}
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center space-x-2">
                                <Switch
                                    id="disable-sidebar"
                                    checked={settings.disabled}
                                    onCheckedChange={(value) =>
                                        dispatch(
                                            setSettings({ disabled: value }),
                                        )
                                    }
                                />
                                <Label htmlFor="disable-sidebar">
                                    Disable Sidebar
                                </Label>
                            </div>
                        </TooltipTrigger>

                        <TooltipContent>
                            <p>Hide sidebar</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </TooltipProvider>
        </ContentLayout>
    );
}
