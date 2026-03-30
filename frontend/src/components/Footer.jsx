import React from 'react';
import { motion } from 'framer-motion';
import { HeartIcon } from '@heroicons/react/24/outline';

export const Footer = () => {
    return (
        <motion.footer
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-r from-slate-950 via-blue-950/30 to-slate-950 border-t-2 border-blue-500/20 backdrop-blur-xl"
        >
            <div className="max-w-[1600px] mx-auto px-6 py-4">
                <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg shadow-lg shadow-blue-500/30">
                            <HeartIcon className="h-4 w-4 text-white" />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-gray-200">Sistema Postventa</p>
                            <p className="text-xs text-gray-400">Gestión de Incidencias Profesional</p>
                        </div>
                    </div>

                    <div className="text-right">
                        <p className="text-xs text-gray-400">© 2025 Polifusión</p>
                        <p className="text-xs text-gray-500">v12.0 - Diseñado con excelencia</p>
                    </div>
                </div>
            </div>
        </motion.footer>
    );
};

export default Footer;
