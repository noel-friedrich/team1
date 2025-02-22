import { getRecentChanges } from "@/lib/articles"

export default function LivePage() {
  const changes = getRecentChanges()

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-3xl font-bold">Live Changes</h1>
      <div className="divide-y rounded-lg border">
        {changes.map((change, i) => (
          <div key={i} className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium">{change.title}</h3>
                <p className="text-sm text-muted-foreground">{change.description}</p>
              </div>
              <time className="text-sm text-muted-foreground">{change.timestamp}</time>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

