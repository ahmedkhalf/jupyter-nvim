local a = vim.api
local M = {}

M.create_jupyter_buffer = function (name, vertical)
  local buf = a.nvim_create_buf(true, true)
  a.nvim_command("buffer " .. buf) -- Focus on buffer
  -- a.nvim_win_set_option(0, "number", false)
  -- a.nvim_win_set_option(0, "signcolumn", "no")
  a.nvim_command("setlocal nonumber")
  a.nvim_command("setlocal signcolumn=no")
  a.nvim_command("setlocal conceallevel=3")
  a.nvim_command("setlocal concealcursor=nvic")

  M.add_syntax("python", "@begin=py@", "@end=py@", 'SpecialComment')
  M.add_syntax("markdown", "@begin=md@", "@end=md@", 'SpecialComment')

  return buf
end

M.add_syntax = function (filetype, startPattern, endPattern, matchgroup)
  local ft = vim.fn.toupper(filetype)
  local group = 'textGroup' .. ft
  if vim.fn.exists('b:current_syntax') == 1 then
    a.nvim_buf_del_var(0, 'current_syntax')
  end

  a.nvim_command('syntax include @' .. group .. ' syntax/' .. filetype .. '.vim')

  local region = ""
  region = region .. 'syntax region textSnip' .. ft
  if matchgroup ~= nil then
    region = region .. " matchgroup=" .. matchgroup
  end
  region = region .. " keepend"
  region = region .. " start=\"" .. startPattern .. "\" end=\"" .. endPattern .. "\""
  region = region .. " contains=@" .. group
  region = region .. " concealends"

  a.nvim_command(region)
end

return M
