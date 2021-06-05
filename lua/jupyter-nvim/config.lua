local M = {}

M.options = {}

M.get_options = function ()
  return M.options
end

local defaults = {
  -- There are currently no options
}

M.setup = function (options)
  M.options = vim.tbl_deep_extend("force", {}, defaults, options or {})
end

M.setup()

return M
