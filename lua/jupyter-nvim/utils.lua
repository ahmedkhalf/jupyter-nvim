local a = vim.api
local cmd = vim.cmd
local M = {}

M.create_jupyter_buffer = function ()
  local bufnr = a.nvim_create_buf(true, false)
  cmd("buffer " .. bufnr) -- Focus on buffer

  cmd("setlocal nonumber")
  cmd("setlocal signcolumn=auto:1-2")
  cmd("setlocal conceallevel=3")
  cmd("setlocal concealcursor=nvic")

  M.add_syntax("python", "@begin=py@", "@end=py@", 'SpecialComment')
  M.add_syntax("markdown", "@begin=md@", "@end=md@", 'SpecialComment')

  a.nvim_buf_set_option(bufnr, "modifiable", false)
  a.nvim_buf_set_option(bufnr, "buftype", "acwrite")

  cmd("au BufWriteCmd <buffer>  call JupiterSave()")

  return bufnr
end

M.add_syntax = function (filetype, startPattern, endPattern, matchgroup)
  local ft = vim.fn.toupper(filetype)
  local group = 'textGroup' .. ft
  if vim.fn.exists('b:current_syntax') == 1 then
    a.nvim_buf_del_var(0, 'current_syntax')
  end

  cmd('syntax include @' .. group .. ' syntax/' .. filetype .. '.vim')

  local region = ""
  region = region .. 'syntax region textSnip' .. ft
  if matchgroup ~= nil then
    region = region .. " matchgroup=" .. matchgroup
  end
  region = region .. " keepend"
  region = region .. " start=\"" .. startPattern .. "\" end=\"" .. endPattern .. "\""
  region = region .. " contains=@" .. group
  region = region .. " concealends"

  cmd(region)
end

M.buf_set_lines = function (bufnr, modified, startIndex, endIndex, strict, replacement)
  a.nvim_buf_set_option(bufnr, "modifiable", true)

  a.nvim_buf_set_lines(bufnr, startIndex, endIndex, strict, replacement)

  a.nvim_buf_set_option(bufnr, "modifiable", false)

  if modified == false then
    a.nvim_buf_set_option(bufnr, "modified", modified)
  end
end

M.print_error = function (msg, beep)
  if beep then
    cmd("execute 'normal! \\<Esc>'")
  end
  cmd("echohl ErrorMsg")
  cmd("echomsg \"" .. msg .. "\"")
  cmd("echohl None")
end

return M
