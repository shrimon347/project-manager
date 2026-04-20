import { SheetMenu } from "@/components/dashboard/sheet-menu";
import { UserNav } from "@/components/dashboard/user-nav";
import { ThemeToggle } from "@/components/theme-toggle";
import { useGetWorkspacesQuery } from "@/store/api/workspaceApi";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { PlusCircle } from "lucide-react";
import { Button } from "../ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { WorkspaceAvatar } from "../workspace/workspace-avatar";

export function Navbar() {
    const { data: workspaces = [], isLoading } = useGetWorkspacesQuery();
    const dispatch = useAppDispatch();

    const selectedWorkspace = useAppSelector(
        (state) => state.workspace.currentWorkspace,
    );

    const handleOnClick = (ws: WorkspaceApi) => {
        dispatch(setWorkspace(ws));
    };
    return (
        <header className="sticky top-0 z-10 w-full bg-background/95 shadow backdrop-blur supports-backdrop-filter:bg-background/60 dark:shadow-secondary">
            <div className="mx-4 sm:mx-8 flex h-14 items-center">
                <div className="flex items-center space-x-4 lg:space-x-0">
                    <SheetMenu />
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant={"outline"}>
                                {selectedWorkspace ? (
                                    <>
                                        {selectedWorkspace.color && (
                                            <WorkspaceAvatar
                                                color={selectedWorkspace.color}
                                                name={selectedWorkspace.name}
                                            />
                                        )}
                                        <span className="font-medium ml-2">
                                            {selectedWorkspace.name}
                                        </span>
                                    </>
                                ) : (
                                    <span className="font-medium">
                                        {isLoading
                                            ? "Loading..."
                                            : "Select Workspace"}
                                    </span>
                                )}
                            </Button>
                        </DropdownMenuTrigger>

                        <DropdownMenuContent>
                            <DropdownMenuLabel>Workspace</DropdownMenuLabel>
                            <DropdownMenuSeparator />

                            <DropdownMenuGroup>
                                {workspaces.map((ws) => (
                                    <DropdownMenuItem
                                        key={ws.id}
                                        onClick={() => handleOnClick(ws)}
                                    >
                                        {ws.color && (
                                            <WorkspaceAvatar
                                                color={ws.color}
                                                name={ws.name}
                                            />
                                        )}
                                        <span className="ml-2">{ws.name}</span>
                                    </DropdownMenuItem>
                                ))}
                            </DropdownMenuGroup>

                            <DropdownMenuGroup>
                                <DropdownMenuItem>
                                    <PlusCircle className="w-4 h-4 mr-2" />
                                    Create Workspace
                                </DropdownMenuItem>
                            </DropdownMenuGroup>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
                <div className="flex flex-1 items-center justify-end gap-2">
                    <ThemeToggle />
                    <UserNav />
                </div>
            </div>
        </header>
    );
}
