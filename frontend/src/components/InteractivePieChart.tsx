"use client";

import { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Sector } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUturnLeftIcon } from '@heroicons/react/24/solid';

interface ChartData {
    name: string;
    value: number;
    color?: string;
    [key: string]: any;
}

interface InteractivePieChartProps {
    data: ChartData[];
    title?: string;
    onSliceClick?: (entry: ChartData) => void;
    onBack?: () => void;
    hasParent?: boolean;
}

const COLORS = ['#3b82f6', '#6366f1', '#818cf8', '#2dd4bf', '#fbbf24', '#f87171', '#a855f7', '#ec4899', '#8b5cf6'];

const renderActiveShape = (props: any) => {
    const RADIAN = Math.PI / 180;
    const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;

    return (
        <g>
            <text x={cx} y={cy} dy={-10} textAnchor="middle" fill="#f8fafc" className="font-black text-[12px] uppercase tracking-wider">
                {payload.name.length > 12 ? payload.name.substring(0, 10) + '..' : payload.name}
            </text>
            <text x={cx} y={cy} dy={15} textAnchor="middle" fill="#94a3b8" className="font-bold text-[10px]">
                {`${value}`}
            </text>
            <Sector
                cx={cx}
                cy={cy}
                innerRadius={innerRadius}
                outerRadius={outerRadius + 6}
                startAngle={startAngle}
                endAngle={endAngle}
                fill={fill}
            />
            <Sector
                cx={cx}
                cy={cy}
                startAngle={startAngle}
                endAngle={endAngle}
                innerRadius={outerRadius + 10}
                outerRadius={outerRadius + 14}
                fill={fill}
            />
        </g>
    );
};

export function InteractivePieChart({ data, title = "Distribución", onSliceClick, onBack, hasParent = false }: InteractivePieChartProps) {
    const [activeIndex, setActiveIndex] = useState(0);

    const onPieEnter = (_: any, index: number) => {
        setActiveIndex(index);
    };

    const handlePieClick = (entry: any, index: number) => {
        if (onSliceClick) {
            onSliceClick(entry);
            setActiveIndex(0);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col h-full bg-transparent overflow-hidden"
        >
            <div className="flex items-center justify-between px-5 pt-5 mb-2">
                <div className="flex items-center gap-2">
                    <div className={`w-1 h-3 rounded-full animate-pulse ${hasParent ? 'bg-emerald-500' : 'bg-blue-500'}`} />
                    <h3 className="text-[11px] font-black text-slate-100 tracking-widest uppercase truncate max-w-[200px]" title={title}>
                        {title}
                    </h3>
                </div>

                <AnimatePresence>
                    {hasParent && (
                        <motion.button
                            initial={{ opacity: 0, x: 10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 10 }}
                            onClick={onBack}
                            className="flex items-center gap-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-black text-[9px] uppercase tracking-widest transition-all shadow-lg border border-white/10"
                        >
                            <ArrowUturnLeftIcon className="h-3 w-3" />
                            Volver
                        </motion.button>
                    )}
                </AnimatePresence>
            </div>

            <div className="flex-1 w-full min-h-0 relative">
                {data && data.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%" debounce={100} minWidth={0} minHeight={0}>
                        <PieChart>
                            <Pie
                                activeIndex={activeIndex}
                                activeShape={renderActiveShape}
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={70}
                                outerRadius={90}
                                dataKey="value"
                                onMouseEnter={onPieEnter}
                                onClick={handlePieClick}
                                animationDuration={800}
                                paddingAngle={4}
                            >
                                {data.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                        stroke="rgba(15, 23, 42, 1)"
                                        strokeWidth={4}
                                        style={{ cursor: !hasParent ? 'pointer' : 'default', outline: 'none' }}
                                    />
                                ))}
                            </Pie>
                            <Tooltip content={<div className="hidden" />} />
                        </PieChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-xs uppercase tracking-widest font-bold">
                        Sin Datos
                    </div>
                )}
            </div>

            {/* Smart Legend with Scroll */}
            <div className="px-5 pb-5 h-[80px] overflow-y-auto custom-scrollbar border-t border-slate-800/50 pt-3">
                <div className="flex flex-wrap justify-center gap-x-4 gap-y-2">
                    {data.map((entry, index) => (
                        <div
                            key={index}
                            className={`flex items-center gap-2 cursor-pointer transition-all group ${activeIndex === index ? 'opacity-100 scale-105' : 'opacity-40 hover:opacity-80'}`}
                            onMouseEnter={() => setActiveIndex(index)}
                            onClick={() => handlePieClick(entry, index)}
                        >
                            <div className="w-2 h-2 rounded-sm rotate-45 shadow-[0_0_5px_currentColor]" style={{ backgroundColor: COLORS[index % COLORS.length], color: COLORS[index % COLORS.length] }} />
                            <span className="text-[10px] font-bold uppercase text-slate-300 tracking-tight truncate max-w-[100px]" title={entry.name}>
                                {entry.name}
                            </span>
                            <span className="text-[9px] font-black text-slate-500">{entry.value}</span>
                        </div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
}
