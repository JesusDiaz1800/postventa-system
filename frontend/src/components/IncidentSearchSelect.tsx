import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Combobox, Transition } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { api, incidentsAPI } from '../services/api';
import { useDebounce } from '../hooks/useDebounce';
import { Incident } from '../types';

interface IncidentSearchSelectProps {
  value: string | number | undefined;
  onChange: (id: number | undefined) => void;
  label?: string;
  placeholder?: string;
  onlyAvailable?: boolean;
}

const IncidentSearchSelect: React.FC<IncidentSearchSelectProps> = ({ 
  value, 
  onChange, 
  label, 
  placeholder = "Buscar incidencia por código o cliente...", 
  onlyAvailable = false 
}) => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);

  // Fetch incidents based on search
  const { data: searchResults, isLoading, refetch } = useQuery<Incident[]>({
    queryKey: ['incidents-search', debouncedQuery, onlyAvailable],
    queryFn: async () => {
      // Si no hay query y no es 'onlyAvailable', devolver vacío
      if (!debouncedQuery && !value && !onlyAvailable) return [];
      
      const params = { 
        search: debouncedQuery,
        page_size: 15
      };

      const response = onlyAvailable 
        ? await api.get('/documents/available-incidents/', { params })
        : await incidentsAPI.list(params);

      // Handle both DRF paginated and direct list responses
      return response.data?.results || (Array.isArray(response.data) ? response.data : []);
    },
    enabled: true 
  });

  // Effect to handle the initial selected value display if it exists but query is empty
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  useEffect(() => {
    if (value && !selectedIncident) {
      // If we have a value but no selected object, try to fetch it specifically or use placeholder
      incidentsAPI.get(value).then(res => {
        setSelectedIncident(res.data);
      }).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const filteredIncidents = Array.isArray(searchResults) ? searchResults : [];

  return (
    <div className="w-full">
      {label && (
        <label className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1.5 ml-1">
          {label}
        </label>
      )}
      <Combobox 
        value={selectedIncident} 
        onChange={(incident: Incident | null) => {
          setSelectedIncident(incident);
          onChange(incident?.id);
        }}
      >
        <div className="relative mt-1">
          <div className="relative w-full cursor-default overflow-hidden rounded-xl bg-white border border-slate-200/60 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all duration-200">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <MagnifyingGlassIcon className="h-4 w-4 text-slate-400" />
            </div>
            <Combobox.Input
              className="w-full border-none py-2.5 pl-10 pr-10 text-sm leading-5 text-slate-900 focus:ring-0 bg-transparent"
              displayValue={(incident: Incident | null) => incident ? `${incident.code} - ${incident.cliente}` : ''}
              onChange={(event) => setQuery(event.target.value)}
              onFocus={(e) => {
                // Forzar apertura al recibir foco si no está abierto
                if (e.target.value === '') {
                   setQuery(''); 
                   if (onlyAvailable) refetch(); // Asegurar datos frescos
                }
              }}
              onClick={(e) => {
                 // Asegurar apertura al hacer clic si está vacío
                 if (query === '') {
                   const button = e.currentTarget.parentElement?.querySelector('button');
                   if (button) button.click();
                 }
              }}
              placeholder={placeholder}
            />
            <Combobox.Button className="absolute inset-y-0 right-0 flex items-center pr-2" id="incidents-dropdown-btn">
              <ChevronUpDownIcon
                className="h-5 w-5 text-slate-400"
                aria-hidden="true"
              />
            </Combobox.Button>
          </div>
          <Transition
            as={React.Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
            afterLeave={() => setQuery('')}
          >
            <Combobox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-xl bg-white py-1 text-base shadow-xl ring-1 ring-black/5 focus:outline-none sm:text-sm z-[50]">
              {isLoading ? (
                <div className="relative cursor-default select-none py-2 px-4 text-slate-500 italic">
                  Buscando...
                </div>
              ) : filteredIncidents.length === 0 && query !== '' ? (
                <div className="relative cursor-default select-none py-2 px-4 text-slate-700">
                  No se encontraron resultados.
                </div>
              ) : (
                filteredIncidents.map((incident) => (
                  <Combobox.Option
                    key={incident.id}
                    className={({ active }) =>
                      `relative cursor-default select-none py-2.5 pl-10 pr-4 ${
                        active ? 'bg-indigo-600 text-white' : 'text-slate-900'
                      }`
                    }
                    value={incident}
                  >
                    {({ selected, active }) => (
                      <>
                        <span className={`block truncate ${selected ? 'font-bold' : 'font-normal'}`}>
                          <span className="font-mono mr-2">[{incident.code}]</span>
                          {incident.cliente}
                        </span>
                        {selected ? (
                          <span
                            className={`absolute inset-y-0 left-0 flex items-center pl-3 ${
                              active ? 'text-white' : 'text-indigo-600'
                            }`}
                          >
                            <CheckIcon className="h-5 w-5" aria-hidden="true" />
                          </span>
                        ) : null}
                      </>
                    )}
                  </Combobox.Option>
                ))
              )}
            </Combobox.Options>
          </Transition>
        </div>
      </Combobox>
    </div>
  );
};

export default IncidentSearchSelect;
