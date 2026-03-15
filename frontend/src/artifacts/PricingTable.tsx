import type { ArtifactData } from '@/types'

interface Props {
  data: ArtifactData
}

export function PricingTable({ data }: Props) {
  const products = data.pricing_products ?? []

  if (products.length === 0) {
    return <p className="text-xs text-gray-500 italic">No pricing data available.</p>
  }

  return (
    <div className="space-y-4">
      {products.map((product) => (
        <div key={product.name}>
          <h5 className="text-xs font-semibold text-white mb-2">{product.name}</h5>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {product.plans.map((plan) => (
              <div
                key={plan.tier}
                className="rounded-lg bg-gray-800/60 border border-gray-700/50 px-3 py-2.5"
              >
                <div className="flex items-baseline justify-between mb-2">
                  <span className="text-xs font-medium text-gray-300 capitalize">
                    {plan.tier}
                  </span>
                  <span className="text-sm font-semibold text-brand-400">{plan.price}</span>
                </div>

                {plan.features.length > 0 && (
                  <ul className="space-y-1">
                    {plan.features.map((feat, i) => (
                      <li key={i} className="flex gap-1.5 text-[11px] text-gray-400 leading-snug">
                        <span className="text-brand-500 shrink-0 mt-px">&#10003;</span>
                        {feat}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
