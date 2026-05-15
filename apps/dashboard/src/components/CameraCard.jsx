import { trackColors } from "../utils/colors"

export default function CameraCard({ title, trackId }) {

  const color = trackColors[trackId] || "#ffffff"

  return (
    <div className="relative bg-gray-900 rounded-xl overflow-hidden h-[300px]">

      <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded text-white z-10">
        {title}
      </div>

      <div
        className="absolute border-4"
        style={{
          borderColor: color,
          top: "80px",
          left: "120px",
          width: "100px",
          height: "180px"
        }}
      >
        <div
          className="text-white px-1"
          style={{
            backgroundColor: color
          }}
        >
          {trackId}
        </div>
      </div>

    </div>
  )
}