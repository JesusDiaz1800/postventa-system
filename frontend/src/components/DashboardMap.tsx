import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useAuth } from '../hooks/useAuth';

// Fix for default marker icons in Leaflet with React
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface CityData {
  city: string;
  count: number;
}

interface DashboardMapProps {
  data: CityData[];
}

const CITY_COORDINATES: { [key: string]: [number, number] } = {
  // Chile
  'SANTIAGO': [-33.4489, -70.6693],
  'VALPARAÍSO': [-33.0472, -71.6127],
  'CONCEPCIÓN': [-36.8201, -73.0444],
  'ANTOFAGASTA': [-23.6509, -70.3975],
  'LA SERENA': [-29.9027, -71.2519],
  'PUERTO MONTT': [-41.4693, -72.9411],
  'TEMUCO': [-38.7397, -72.5901],
  'RANCAGUA': [-34.1708, -70.7444],
  'TALCA': [-35.4264, -71.6554],
  'IQUIQUE': [-20.2133, -70.1503],
  'COPIAPÓ': [-27.3667, -70.3333],
  'ARICA': [-18.4746, -70.2975],
  // Perú
  'LIMA': [-12.0464, -77.0428],
  'AREQUIPA': [-16.4090, -71.5375],
  'TRUJILLO': [-8.1160, -79.0300],
  // Colombia
  'BOGOTÁ': [4.7110, -74.0721],
  'MEDELLÍN': [6.2442, -75.5812],
  'CALI': [3.4516, -76.5320],
};

const COUNTRY_CONFIG: { [key: string]: { center: [number, number], zoom: number } } = {
  'CL': { center: [-33.4489, -70.6693], zoom: 5 },
  'CO': { center: [4.7110, -74.0721], zoom: 6 },
  'PE': { center: [-12.0464, -77.0428], zoom: 6 },
};

// Componente para actualizar vista dinámicamente
const ChangeView = ({ center, zoom }: { center: [number, number], zoom: number }) => {
  const map = useMap();
  map.setView(center, zoom);
  return null;
};

const DashboardMap: React.FC<DashboardMapProps> = ({ data }) => {
  const { user } = useAuth();
  const country = user?.country_code || 'CL';
  const { center: defaultCenter, zoom: defaultZoom } = COUNTRY_CONFIG[country] || COUNTRY_CONFIG['CL'];

  const mapData = data?.map(item => {
    const cityUpper = item.city?.toUpperCase() || '';
    return {
      ...item,
      coords: CITY_COORDINATES[cityUpper] || defaultCenter
    };
  }) || [];

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden border border-slate-200 shadow-inner bg-slate-50">
      <MapContainer 
        center={defaultCenter} 
        zoom={defaultZoom} 
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <ChangeView center={defaultCenter} zoom={defaultZoom} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {mapData.map((city, idx) => (
          <CircleMarker 
            key={idx}
            center={city.coords}
            radius={Math.min(15, 5 + city.count * 2)}
            pathOptions={{ 
              fillColor: '#3b82f6', 
              color: '#1d4ed8', 
              weight: 2, 
              fillOpacity: 0.6 
            }}
          >
            <Popup>
              <div className="p-1">
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">{city.city}</p>
                <p className="text-sm font-black text-slate-900">{city.count} Visitas</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default DashboardMap;
