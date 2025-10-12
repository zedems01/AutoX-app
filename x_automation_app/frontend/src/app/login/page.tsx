"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { useRouter, useSearchParams } from "next/navigation"
import { toast } from "sonner"
import React, { Suspense, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { login } from "@/lib/api"
import { Loader2 } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"


const formSchema = z.object({
  user_name: z.string().min(1, { message: "Username is required." }),
  email: z.string().email({ message: "Invalid email address." }),
  password: z.string().min(1, { message: "Password is required." }),
  proxy: z.string().url({ message: "Please enter a valid proxy URL." }),
  totp_secret: z.string().min(1, { message: "TOTP secret is required." }),
})

function Login() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login: authLogin } = useAuth()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      user_name: "",
      email: "",
      password: "",
      proxy: "",
      totp_secret: "",
    },
  })

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      toast.success("Login successful!", { duration: 5000 })
      authLogin(data)

      const redirect = searchParams.get('redirect')
      const workflowState = searchParams.get('workflowState')

      if (redirect) {
        let redirectUrl = redirect
        if (workflowState) {
          redirectUrl += `?workflowState=${workflowState}`
        }
        router.push(redirectUrl)
      } else {
        router.push("/")
      }
    },
    onError: (error) => {
      toast.error(`Login failed: ${error.message}`, { duration: 15000 })
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    mutation.mutate(values)
  }

  return (
    <div className="flex justify-center items-start min-h-screen px-4 py-6 md:py-12">
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="pb-4 md:pb-6">
          <CardTitle className="text-lg md:text-xl text-center">X Session Login</CardTitle>
          <CardDescription className="text-center text-sm md:text-base">
            Enter your credentials and a proxy to start the process.
          </CardDescription>
        </CardHeader>
        <CardContent className="px-4 md:px-6 pb-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 md:space-y-6">
              <FormField
                control={form.control}
                name="user_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">Username</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="your_username" 
                        {...field} 
                        className="h-10 md:h-11"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">Email</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="user@example.com" 
                        {...field} 
                        className="h-10 md:h-11"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">Password</FormLabel>
                    <FormControl>
                      <Input 
                        type="password" 
                        placeholder="••••••••" 
                        {...field} 
                        className="h-10 md:h-11"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="proxy"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">Proxy</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="http://user:pass@ip:port" 
                        {...field} 
                        className="h-10 md:h-11"
                      />
                    </FormControl>
                    <FormDescription className="text-xs md:text-sm text-muted-foreground">
                      Your proxy for the X connection.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="totp_secret"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">TOTP Secret</FormLabel>
                    <FormControl>
                      <Input 
                        type="password" 
                        placeholder="••••••••" 
                        {...field} 
                        className="h-10 md:h-11"
                      />
                    </FormControl>
                    <FormDescription className="text-xs md:text-sm text-muted-foreground">
                      Your Time-based One-Time Password secret.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button 
                type="submit" 
                className="w-full cursor-pointer h-10 md:h-11 text-sm md:text-base font-medium mt-6" 
                disabled={mutation.isPending}
              >
                {mutation.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Login
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Login />
    </Suspense>
  )
} 