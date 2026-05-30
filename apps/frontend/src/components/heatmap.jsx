import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Polygon, Tooltip } from "react-leaflet";
import { Loader2, Info } from "lucide-react";

const COLOR_MAP = {
  green: "#22c55e",
  orange: "#fb923c",
  red: "#ef4444",
  gray: "#9ca3af",
};

export function Heatmap({ convertedConjs, loading }) {
  function defineColor(conj) {
    if (!conj.limit || !conj.accumulated_value) return "gray";
    const { limit, accumulated_value: value } = conj;
    if (value >= limit) return "red";
    if (value >= limit / 2) return "orange";
    return "green";
  }

  function getPathOptions(conj) {
    const key = defineColor(conj);
    return { color: COLOR_MAP[key], fillColor: COLOR_MAP[key], fillOpacity: 0.4, weight: 2 };
  }

  function invertCoordinates(coordinates) {
    return coordinates.map(([x, y]) => [y, x]);
  }

  function getCoordinateCenter(conjArray) {
    if (conjArray && conjArray.length > 0) {
      const conj = conjArray[0];
      if (conj?.coordinates) {
        return [conj.coordinates[0][1], conj.coordinates[0][0]];
      }
    }
    return [-22.97, -45.5];
  }

  function formatValue(value) {
    if (value == null) return "—";
    return typeof value === "number" ? value.toFixed(2) : value;
  }

  const hasData = convertedConjs && convertedConjs.length > 0 && convertedConjs[0]?.coordinates;

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={getCoordinateCenter(convertedConjs)}
        zoom={9}
        scrollWheelZoom
        style={{ width: "100%", height: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {hasData && convertedConjs.map((conj, index) => {
          if (!conj.coordinates) return null;
          return (
            <Polygon
              key={index}
              pathOptions={getPathOptions(conj)}
              positions={invertCoordinates(conj.coordinates)}
            >
              <Tooltip>
                <div className="text-xs flex flex-col gap-0.5">
                  <span className="font-semibold">{conj.name || "—"}</span>
                  <span>Indicador: {conj.indicator_type_code || "—"}</span>
                  <span>Limite: {formatValue(conj.limit)}</span>
                  <span>Valor acumulado: {formatValue(conj.accumulated_value)}</span>
                </div>
              </Tooltip>
            </Polygon>
          );
        })}
      </MapContainer>

      {loading && (
        <div className="absolute inset-0 z-1000 flex items-center justify-center bg-background/60 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="text-sm">Carregando dados...</span>
          </div>
        </div>
      )}

      {!loading && !hasData && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-1000">
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card border border-border shadow-md text-sm text-muted-foreground">
            <Info className="w-4 h-4 shrink-0" />
            Sem dados para o período selecionado
          </div>
        </div>
      )}
    </div>
  );
}
