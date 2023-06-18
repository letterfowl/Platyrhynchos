import { createClient } from '@supabase/supabase-js'

const DB = createClient("https://tecskhekxfsziaiqpuxj.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlY3NraGVreGZzemlhaXFwdXhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ2NzA1MjEsImV4cCI6MjAwMDI0NjUyMX0.qIZePGL2cSyY4akQgo_hm3Zemnn0YUwxaSaZqF_crUk")

export async function getRandom(max_size) {
    const { data, error } = await DB.rpc('get_random', {max_size: max_size})
    if (error != null) {
        console.error(error)
    }
    return [data]
}

export async function getRegex(regex, previous) {
    const { data, error } = await DB.rpc('get_regex', {json_data: {regex: regex, previous: previous.split(",")}})
    if (error != null) {
        console.error(error)
    }
    return data
}

export async function getRegexWithAlphabit(regex, alphabit, previous) {
    const { data, error } = await DB.rpc('get_regex_w_alphabit', {json_data: {regex: regex, alphabit: alphabit, previous: previous.split(",")}})
    if (error != null) {
        console.error(error)
    }
    return data
}