import { useState } from "react";
import {
    TrendingUp,
    TrendingDown,
    Calendar as CalendarIcon,
    Filter,
    BarChart3,
    Zap,
    ChevronLeft,
    ChevronRight,
    Info,
} from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
} from "recharts";
import { apiClient } from "@/api/client";
import { Heatmap } from "../../../components/heatmap";

export function HeatmapFilters() {
    const [selectedTab, setSelectedTab] = useState("dec");

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4 justify-between">
                <div className="flex gap-2">
                    <Button
                        variant={selectedTab === "dec" ? "default" : "outline"}
                        onClick={() => setSelectedTab("dec")}
                        className={
                            selectedTab === "dec"
                                ? "bg-primary text-primary-foreground"
                                : "border-border text-foreground hover:bg-muted"
                        }
                    >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        DEC
                    </Button>
                    <Button
                        variant={selectedTab === "fec" ? "default" : "outline"}
                        onClick={() => setSelectedTab("fec")}
                        className={
                            selectedTab === "fec"
                                ? "bg-primary text-primary-foreground"
                                : "border-border text-foreground hover:bg-muted"
                        }
                    >
                        <Zap className="w-4 h-4 mr-2" />
                        FEC
                    </Button>
                </div>
            </div>

            <Heatmap/>
        </div>
    )

}