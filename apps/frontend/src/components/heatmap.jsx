"use client";

import "../App.css"
import "@/index.css" // Ensure base classes are present if needed
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, Popup, Polygon } from 'react-leaflet'

export function Heatmap({ convertedConjs }) {

    const purpleOptions = { color: 'purple' }

    function invertCoordinates(coordinates) {
        return coordinates.map(([x, y]) => [
            y,
            x
        ]);
    } 

    function mappedPolygons(conj) {
        if (conj.coordinates) {
            let coordinates = conj.coordinates
            coordinates = invertCoordinates(coordinates)
            return (
                <Polygon pathOptions={purpleOptions} positions={coordinates} />
            )
        }

        return (<></>)
    }

    return (
        <>
            <MapContainer center={[-22.943924476033715, -45.51313686727258]} zoom={13} scrollWheelZoom={false}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[51.505, -0.09]}>
                    <Popup>
                        A pretty CSS3 popup. <br /> Easily customizable.
                    </Popup>
                </Marker>
                
                {convertedConjs.map(mappedPolygons)}
            </MapContainer>
        </>
    )
}