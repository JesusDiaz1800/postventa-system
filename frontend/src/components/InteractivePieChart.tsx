"use client";

import { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ChevronLeft } from 'lucide-react';

interface CategoryData {
    name: string;
    value: number;
    color: string;
    subcategories?: SubcategoryData[];
}

interface SubcategoryData {
    name: string;
    value: number;
    color: string;
}

interface InteractivePieChartProps {
    data: CategoryData[];
}

export function InteractivePieChart({ data }: InteractivePieChartProps) {
    const [selectedCategory, setSelectedCategory] = useState<CategoryData | null>(null);
    const [isAnimating, setIsAnimating] = useState(false);

    const handlePieClick = (entry: any, index: number) => {
        if (selectedCategory) return; // Ya estamos en subcategorías

        const category = data[index];
        if (category.subcategories && category.subcategories.length > 0) {
            setIsAnimating(true);
            setTimeout(() => {
                setSelectedCategory(category);
                setIsAnimating(false);
            }, 200);
        }
    };

    const handleBack = () => {
        setIsAnimating(true);
        setTimeout(() => {
            setSelectedCategory(null);
            setIsAnimating(false);
        }, 200);
    };

    const currentData = selectedCategory?.subcategories || data;
    const title = selectedCategory ? selectedCategory.name : 'Distribución por Categorías';

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white/95 backdrop-blur-sm px-4 py-2 rounded-xl shadow-xl border border-slate-200">
                    <p className="text-sm font-semibold text-slate-800">{payload[0].name}</p>
                    <p className="text-xs text-blue-600 font-bold">{payload[0].value} incidencias</p>
                    <p className="text-xs text-slate-500">
                        {((payload[0].value / currentData.reduce((acc, item) => acc + item.value, 0)) * 100).toFixed(1)}%
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="relative bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-lg p-6 h-full transition-all duration-300 hover:shadow-xl hover:border-slate-300/60">
            {/* Header con título y botón back */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-indigo-500 rounded-full"></div>
                    {title}
                </h3>
                {selectedCategory && (
                    <button
                        onClick={handleBack}
                        className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                        <ChevronLeft size={16} />
                        Volver
                    </button>
                )}
            </div>

            {/* Indicador de drill-down activo */}
            {selectedCategory && (
                <div className="mb-3 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-700 font-medium">
                        📊 Subcategorías de <span className="font-bold">{selectedCategory.name}</span>
                    </p>
                </div>
            )}

            {/* Gráfico de torta */}
            <div className={`transition-opacity duration-200 ${isAnimating ? 'opacity-30' : 'opacity-100'}`}>
                <ResponsiveContainer width="100%" height={320}>
                    <PieChart>
                        <Pie
                            data={currentData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                            outerRadius={100}
                            innerRadius={selectedCategory ? 50 : 0}
                            fill="#8884d8"
                            dataKey="value"
                            onClick={handlePieClick}
                            cursor={!selectedCategory ? "pointer" : "default"}
                            animationBegin={0}
                            animationDuration={800}
                        >
                            {currentData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.color}
                                    className="transition-all duration-200 hover:opacity-80"
                                />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                            formatter={(value, entry: any) => (
                                <span className="text-sm text-slate-700 font-medium">{value}</span>
                            )}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Hint para interacción */}
            {!selectedCategory && (
                <div className="mt-3 text-center">
                    <p className="text-xs text-slate-500 italic">
                        💡 Haz click en una categoría para ver sus subcategorías
                    </p>
                </div>
            )}
        </div>
    );
}
