import React from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { ExclamationTriangleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

const LogoutModal = ({ isOpen, onClose, onConfirm }) => {
    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-[99999]" onClose={onClose}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" />
                </Transition.Child>

                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4 text-center">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 scale-95"
                            enterTo="opacity-100 scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 scale-100"
                            leaveTo="opacity-0 scale-95"
                        >
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-[2rem] bg-white p-6 text-left align-middle shadow-2xl transition-all border border-slate-100">
                                <div className="flex flex-col items-center text-center space-y-4">
                                    <div className="w-16 h-16 bg-rose-50 rounded-full flex items-center justify-center mb-2">
                                        <ArrowRightOnRectangleIcon className="w-8 h-8 text-rose-600" />
                                    </div>

                                    <Dialog.Title
                                        as="h3"
                                        className="text-xl font-black text-slate-900 uppercase italic tracking-tight"
                                    >
                                        ¿Cerrar Sesión?
                                    </Dialog.Title>

                                    <div className="mt-2 text-sm text-slate-500 font-medium">
                                        <p>Al confirmar, su sesión actual se cerrará y será redirigido a la pantalla de acceso.</p>
                                    </div>

                                    <div className="mt-6 flex gap-3 w-full">
                                        <button
                                            type="button"
                                            className="flex-1 px-4 py-3 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-bold uppercase hover:bg-slate-50 transition-colors"
                                            onClick={onClose}
                                        >
                                            Cancelar
                                        </button>
                                        <button
                                            type="button"
                                            className="flex-1 px-4 py-3 bg-rose-600 border border-rose-600 text-white rounded-xl text-sm font-bold uppercase hover:bg-rose-700 shadow-lg shadow-rose-200 transition-all hover:shadow-xl active:scale-95"
                                            onClick={onConfirm}
                                        >
                                            Sí, Salir
                                        </button>
                                    </div>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};

export default LogoutModal;
