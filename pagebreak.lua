-- Inserta \newpage antes de cada encabezado de nivel 1 (capítulos),
-- excepto antes del primero, para que cada capítulo inicie en página nueva.
local first = true
function Header(el)
  if el.level == 1 then
    if first then
      first = false
    else
      return { pandoc.RawBlock('latex', '\\newpage'), el }
    end
  end
end
