import React, { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { ChevronUpDownIcon } from '@heroicons/react/24/outline';

export interface SelectOption {
    value: string | number;
    label: string;
}

export interface ModernSelectProps {
    value: string | number | null;
    onChange: (value: any) => void;
    options: SelectOption[];
    label?: string;
    placeholder?: string;
}

const ModernSelect: React.FC<ModernSelectProps> = ({ 
    value, 
    onChange, 
    options, 
    label, 
    placeholder = 'Seleccionar' 
}) => {
    const selectedOption = options.find(opt => opt.value === value);

    return (
        <div className="relative">
            {label && (
                <span className="block text-[9px] uppercase font-bold text-slate-400 tracking-wider mb-1 ml-1">
                    {label}
                </span>
            )}
            <Listbox value={value} onChange={onChange}>
                <div className="relative mt-0.5">
                    <Listbox.Button className="relative w-full cursor-pointer rounded-xl bg-white/60 pl-3 pr-8 py-1.5 text-left border border-slate-200/60 focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-xs">
                        <span className={`block truncate ${!selectedOption ? 'text-slate-400' : 'text-slate-700 font-medium'}`}>
                            {selectedOption ? selectedOption.label : placeholder}
                        </span>
                        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                            <ChevronUpDownIcon
                                className="h-4 w-4 text-slate-400"
                                aria-hidden="true"
                            />
                        </span>
                    </Listbox.Button>
                    <Transition
                        as={Fragment}
                        leave="transition ease-in duration-100"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                    >
                        <Listbox.Options
                            anchor="bottom start"
                            className="absolute mt-1 max-h-60 min-w-[100px] overflow-auto rounded-xl bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm z-[9999]"
                        >
                            {options.map((option, personIdx) => (
                                <Listbox.Option
                                    key={personIdx}
                                    className={({ active }) =>
                                        `relative cursor-default select-none py-2 pl-3 pr-4 ${active ? 'bg-indigo-50 text-indigo-900' : 'text-slate-900'
                                        }`
                                    }
                                    value={option.value}
                                >
                                    {({ selected }) => (
                                        <>
                                            <span
                                                className={`block truncate ${selected ? 'font-bold text-indigo-600' : 'font-normal'
                                                    }`}
                                            >
                                                {option.label}
                                            </span>
                                        </>
                                    )}
                                </Listbox.Option>
                            ))}
                        </Listbox.Options>
                    </Transition>
                </div>
            </Listbox>
        </div>
    );
};

export default ModernSelect;
