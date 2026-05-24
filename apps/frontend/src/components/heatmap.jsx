"use client";

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import "../App.css"
import "@/index.css" // Ensure base classes are present if needed
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, Popup, Polygon, Tooltip } from 'react-leaflet'

export function Heatmap({ convertedConjs }) {

    function defineColor(conj) {
        let colorString = 'gray'
        if (conj.limit && conj.accumulated_value) {
            let limit = conj.limit
            let halfLimit = limit / 2
            let value = conj.accumulated_value

            if (value < halfLimit) {
                colorString = 'green'
            }

            if (value >= halfLimit) {
                colorString = 'orange'
            }

            if (value >= limit) {
                colorString = 'red'
            }
        }
        return { color: colorString }
    }

    function invertCoordinates(coordinates) {
        return coordinates.map(([x, y]) => [
            y,
            x
        ]);
    }

    function mappedPolygons(conj) {
        if (conj.coordinates) {
            // let coordinates = conj.coordinates
            let {coordinates, ...rest} = conj
            coordinates = invertCoordinates(coordinates)
            let informationString = JSON.stringify(rest)
            return (
                <Polygon pathOptions={defineColor(conj)} positions={coordinates}>
                     <Tooltip>
                        Name: {conj.name}
                        <br />
                        Indicator Type: {conj.indicator_type_code}
                        <br />
                        Limit: {conj.limit}
                        <br />
                        Accumulated Value: {conj.accumulated_value}
                     </Tooltip>
                </Polygon>
            )
        }

        return (<></>)
    }

    function getCoordinateCenter(conjArray) {
        if (conjArray) {
            let conj = conjArray[0]
            if (conj.coordinates) {
                let firstCoordinate = [conj.coordinates[0][1], conj.coordinates[0][0]]
                return firstCoordinate
            }
            return [51.505, -0.09]
        }

    }

    function colorLabels() {
        return (
            <Card className="max-w-[10vw] bg-card border-border">
                <CardContent>
                    <div className="text-2xl font-bold text-foreground">
                        Labels
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                        <span className="text-sm text-muted-foreground">
                            🔴 Critical
                        </span>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                        <span className="text-sm text-muted-foreground">
                            🟠 Attention
                        </span>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                        <span className="text-sm text-muted-foreground">
                            🟢 Normal
                        </span>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                        <span className="text-sm text-muted-foreground">
                            ⚪ No Data
                        </span>
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <>
            {convertedConjs && convertedConjs[0].coordinates && (
                <MapContainer center={getCoordinateCenter(convertedConjs)} zoom={9} scrollWheelZoom={true}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <Marker position={[51.505, -0.09]}>
                        <Popup>
                            A pretty CSS3 popup. <br /> Easily customizable.
                        </Popup>
                    </Marker>

                    <div className={'leaflet-bottom leaflet-right'}>
                        <div className="leaflet-control leaflet-bar">{colorLabels()}</div>
                    </div>

                    {convertedConjs.map(mappedPolygons)}
                </MapContainer>
            )}


        </>
    )
}