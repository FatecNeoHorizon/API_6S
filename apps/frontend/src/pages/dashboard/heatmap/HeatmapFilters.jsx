import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  Calendar as CalendarIcon,
  Filter,
  BarChart2,
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
import { Calendar } from "@/components/ui/calendar"
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
import { getConj } from "../../../api/heatmap";
import { Heatmap } from "../../../components/heatmap";

export function HeatmapFilters() {
  const [selectedTab, setSelectedTab] = useState("DEC");
  const [decFecPopoverOpen, setDecFecPopoverOpen] = useState(false);

  const [selectedDate, setSelectedDate] = useState(new Date())
  const [selectedYear, setSelectedYear] = useState(null)
  const [selectedMonth, setSelectedMonth] = useState(null)

  const [convertedConjs, setConvertedConjs] = useState([{
    name: null,
    indicator_type_code: null,
    year: null,
    limit: null,
    accumulated_value: null,
    periods_count: null,
    coordinates: null,
  },])

  const fetchConj = async () => {
    // setDecFecLoading(true);
    const options =
    {
      year: selectedYear ? selectedYear : 2023,
      indicator_type_code: selectedTab
    }
    try {
      const data = await getConj(options);
      if (typeof data === "string") {
        console.error("[geo/conj] Expected JSON, got text:", data);
        setConvertedConjs(null)
        return;
      }
      // setTamTotal(payload?.tam_total ?? null)
      setConvertedConjs(data)
    } catch (error) {
      console.error("[geo/conj] Erro:", error);
    } finally {
      // setDecFecLoading(false);
    }
  }

  const mockedCoordinates = [
    [
      -45.51313686727258,
      -22.943924476033715
    ],
    [
      -45.51021288891366,
      -22.938418193344887
    ],
    [
      -45.504575803430555,
      -22.936958280700026
    ]
  ]

  const mockedCoordinatesTwo = [
    [
      -45.49876223858638,
      -22.938541489498107
    ],
    [
      -45.49192705468977,
      -22.943170336042158
    ],
    [
      -45.489313371215076,
      -22.949727000800408
    ],
    [
      -45.49082067363514,
      -22.953679910599362
    ],
    [
      -45.49081609788459,
      -22.953709192525196
    ],
    [
      -45.48871966847787,
      -22.955925112154148
    ],
    [
      -45.485420975897284,
      -22.957337655708216
    ],
    [
      -45.48311888053189,
      -22.957276663687026
    ],
    [
      -45.48009828530758,
      -22.95625333142607
    ],
    [
      -45.47725817412538,
      -22.955197511156143
    ],
    [
      -45.47499692237005,
      -22.954167639025286
    ],
    [
      -45.47366138056822,
      -22.953949774662306
    ],
    [
      -45.47231387058861,
      -22.953654790735982
    ],
    [
      -45.469696311935195,
      -22.95340249402983
    ],
    [
      -45.46929605516874,
      -22.962241210063723
    ],
    [
      -45.4692800814106,
      -22.972366561867318
    ],
    [
      -45.47115842252316,
      -22.97579724434729
    ],
    [
      -45.471609150142115,
      -22.97593953238345
    ],
    [
      -45.48240252555604,
      -22.9772981750707
    ],
    [
      -45.486310287589674,
      -22.98253328338427
    ],
    [
      -45.48660963862386,
      -22.99242646530911
    ],
    [
      -45.48743014498518,
      -22.995290366257336
    ],
    [
      -45.49133836297506,
      -22.99578722460069
    ],
    [
      -45.4956233564327,
      -22.9996565316236
    ],
    [
      -45.497842537003464,
      -22.99707962412532
    ],
    [
      -45.50018252710191,
      -22.993761580832256
    ],
    [
      -45.50215225911944,
      -22.990900853591484
    ],
    [
      -45.50300410145809,
      -22.98765071091151
    ],
    [
      -45.50330030036855,
      -22.984908188761835
    ],
    [
      -45.50378720681408,
      -22.98308193098626
    ],
    [
      -45.50341003024863,
      -22.982003659141526
    ],
    [
      -45.5024747991726,
      -22.98097683930962
    ],
    [
      -45.50221907425083,
      -22.979442001447183
    ],
    [
      -45.502771941471906,
      -22.97841046017453
    ],
    [
      -45.50388585524797,
      -22.980059552406374
    ],
    [
      -45.506475410811504,
      -22.98324698086344
    ],
    [
      -45.51267483067886,
      -22.985526993376027
    ],
    [
      -45.51435823744265,
      -22.986767308664298
    ],
    [
      -45.516687950988114,
      -22.98610726114117
    ],
    [
      -45.51768935777761,
      -22.985029673680458
    ],
    [
      -45.51801797454982,
      -22.98467603327225
    ],
    [
      -45.51802097109089,
      -22.984617669070133
    ],
    [
      -45.516951593541194,
      -22.98198445771652
    ],
    [
      -45.517341441554265,
      -22.978547222776058
    ],
    [
      -45.51888525465074,
      -22.977223507958456
    ],
    [
      -45.52167524751462,
      -22.978923524301138
    ],
    [
      -45.528305502896615,
      -22.985005567353028
    ],
    [
      -45.53091281917125,
      -22.984629293706917
    ],
    [
      -45.534219675797374,
      -22.981900906201815
    ],
    [
      -45.537809640802266,
      -22.97907962322597
    ],
    [
      -45.540719108599944,
      -22.976190846130578
    ],
    [
      -45.538180150693336,
      -22.972396780886697
    ],
    [
      -45.53915264337974,
      -22.969779358930225
    ],
    [
      -45.53980995966185,
      -22.969680648443102
    ],
    [
      -45.54081871121451,
      -22.970084698549954
    ],
    [
      -45.54182637998343,
      -22.970239790234075
    ],
    [
      -45.542771225711476,
      -22.970883606792995
    ],
    [
      -45.54362657090945,
      -22.97036795171954
    ],
    [
      -45.54405517340746,
      -22.97159833849247
    ],
    [
      -45.5444860359018,
      -22.96971352855644
    ],
    [
      -45.54430831907365,
      -22.969525073823036
    ],
    [
      -45.543864749158786,
      -22.96889246551484
    ],
    [
      -45.543751100033205,
      -22.968673077700316
    ],
    [
      -45.54473177115426,
      -22.968324914163418
    ]
  ]

  const mockedDataTest = [
    {
      name: "ARATEMA",
      indicator_type_code: "FEC",
      year: 2012,
      limit: 7,
      accumulated_value: 9,
      periods_count: 8,
      coordinates: mockedCoordinates,
    },
    {
      name: "TRAVERSE TOWN",
      indicator_type_code: "DEC",
      year: 2012,
      limit: 10,
      accumulated_value: 4,
      periods_count: 8,
      coordinates: mockedCoordinatesTwo,
    },
  ]

  useEffect(() => {

    setSelectedMonth(selectedDate.getMonth() + 1)
    setSelectedYear(selectedDate.getFullYear())

    fetchConj()
    // setConvertedConjs(mockedDataTest);
  }, [selectedTab, selectedDate])

  return (
    <div className="grid grid-cols-[3fr_7fr] gap-4">
      <div className="grid grid-cols-2 gap-4 justify-between">
        <div className="col-span-2 gap-2">
          <Button
            variant={selectedTab === "DEC" ? "default" : "outline"}
            onClick={() => setSelectedTab("DEC")}
            className={
              selectedTab === "DEC"
                ? "bg-primary text-primary-foreground"
                : "border-border text-foreground hover:bg-muted"
            }
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            DEC
          </Button>
          <Button
            variant={selectedTab === "FEC" ? "default" : "outline"}
            onClick={() => setSelectedTab("FEC")}
            className={
              selectedTab === "FEC"
                ? "bg-primary text-primary-foreground"
                : "border-border text-foreground hover:bg-muted"
            }
          >
            <BarChart2 className="w-4 h-4 mr-2" />
            FEC
          </Button>
        </div>

        <div>
          <Popover
            open={decFecPopoverOpen}
            onOpenChange={setDecFecPopoverOpen}
            className="gap-2 bg-primary text-primary-foreground"
          >
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 border-border text-foreground hover:bg-muted"
              >
                <CalendarIcon className="w-4 h-4 mr-2" />
                "Personalizado"
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                className="select-none transition-colors text-foreground"
                captionLayout="dropdown"
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      <Heatmap convertedConjs={convertedConjs} />
    </div>
  )

}