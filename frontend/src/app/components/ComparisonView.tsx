import React from 'react';
import ReactCompareImage from 'react-compare-image';

interface ComparisonViewProps {
    leftImage: string;
    rightImage: string;
}

const ComparisonView: React.FC<ComparisonViewProps> = ({ leftImage, rightImage }) => {
    return (
        <div className="w-full max-w-4xl mx-auto rounded-xl overflow-hidden shadow-2xl border-4 border-gray-100">
            <ReactCompareImage
                leftImage={leftImage}
                rightImage={rightImage}
                leftImageLabel="ORIGINAL"
                rightImageLabel="TRADUCIDO"
                sliderLineColor="#3B82F6" // Blue-500
                sliderLineWidth={3}
                handleSize={40}
                hover={true} // Enable mouse follow
            />
            <div className="bg-gray-50 p-3 text-center text-sm text-gray-500 font-medium border-t">
                ↔️ Desliza para comparar el resultado
            </div>
        </div>
    );
};

export default ComparisonView;
